import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import AppLayout from '../components/AppLayout';
import Button from '../components/Button';
import { useToast } from '../components/ToastContext';

interface ApiKeysForm {
  monsterId: string;
  monsterSecret: string;
  indeedKey: string;
  docAiId: string;
}

const parserOptions = [
  { value: 'pyresparser', label: 'pyresparser' },
  { value: 'google-docai', label: 'Google Document AI' },
  { value: 'gpt4-text', label: 'GPT-4 text parse' },
];

const Settings: React.FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<ApiKeysForm>({
    defaultValues: {
      monsterId: '',
      monsterSecret: '',
      indeedKey: '',
      docAiId: '',
    },
  });

  const [parser, setParser] = React.useState('pyresparser');
  const [isLoading, setIsLoading] = React.useState(true);
  const { addToast } = useToast();

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get('/api/settings');
        setParser(response.data.parser);
      } catch (error) {
        console.error("Failed to fetch settings", error);
        addToast({
          title: 'Error',
          description: 'Failed to load settings. Please try again.',
          variant: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchSettings();
  }, [addToast]);

  const onApiKeysSubmit = (data: ApiKeysForm) => {
    console.log('API Keys:', data);
  };

  const handleParserChange = async (newParser: string) => {
    setParser(newParser);
    try {
      await axios.post('/api/settings', { parser: newParser });
      addToast({
        title: 'Success',
        description: 'Parser settings saved successfully!',
        variant: 'success',
      });
    } catch (error) {
      console.error("Failed to save settings", error);
      addToast({
        title: 'Error',
        description: 'Failed to save settings. Please try again.',
        variant: 'error',
      });
    }
  };

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto space-y-8 p-6">
        {/* API Keys Section */}
        <section aria-labelledby="api-keys-heading">
          <h2 id="api-keys-heading" className="text-xl font-semibold mb-4">API Keys</h2>
          <form onSubmit={handleSubmit(onApiKeysSubmit)} className="space-y-6">
            <div>
              <label htmlFor="monsterId" className="block mb-1 font-medium">Monster Client ID</label>
              <input
                id="monsterId"
                {...register('monsterId', { required: true })}
                className="block w-full border rounded-lg px-3 py-2 mb-4"
                type="text"
                autoComplete="off"
              />
            </div>
            <div>
              <label htmlFor="monsterSecret" className="block mb-1 font-medium">Monster Client Secret</label>
              <input
                id="monsterSecret"
                {...register('monsterSecret', { required: true })}
                className="block w-full border rounded-lg px-3 py-2 mb-4"
                type="password"
                autoComplete="off"
              />
            </div>
            <div>
              <label htmlFor="indeedKey" className="block mb-1 font-medium">Indeed API Key</label>
              <input
                id="indeedKey"
                {...register('indeedKey', { required: true })}
                className="block w-full border rounded-lg px-3 py-2 mb-4"
                type="text"
                autoComplete="off"
              />
            </div>
            <div>
              <label htmlFor="docAiId" className="block mb-1 font-medium">GCP Document AI Processor ID</label>
              <input
                id="docAiId"
                {...register('docAiId', { required: true })}
                className="block w-full border rounded-lg px-3 py-2 mb-4"
                type="text"
                autoComplete="off"
              />
            </div>
            <Button type="submit" variant="primary">Save API Keys</Button>
          </form>
        </section>

        {/* Parser Choice Section */}
        <section aria-labelledby="parser-choice-heading">
          <h2 id="parser-choice-heading" className="text-xl font-semibold mb-4">Parser Choice</h2>
          <div className={isLoading ? 'opacity-50 pointer-events-none' : ''}>
            <fieldset>
              <legend className="sr-only">Parser Choice</legend>
              <div className="space-y-3 mb-4">
                {parserOptions.map(opt => (
                  <label key={opt.value} className="inline-flex items-center mb-3 cursor-pointer">
                    <span className="relative mr-2">
                      <input
                        type="radio"
                        name="parser"
                        value={opt.value}
                        checked={parser === opt.value}
                        onChange={() => handleParserChange(opt.value)}
                        className="sr-only"
                        aria-checked={parser === opt.value}
                        aria-labelledby={`parser-${opt.value}`}
                        disabled={isLoading}
                      />
                      <span
                        className={`w-4 h-4 border-2 rounded-full flex items-center justify-center ${parser === opt.value ? 'border-primary' : 'border-gray-400'}`}
                        style={{ display: 'inline-block' }}
                      >
                        {parser === opt.value && (
                          <span className="w-2 h-2 bg-primary rounded-full block" />
                        )}
                      </span>
                    </span>
                    <span id={`parser-${opt.value}`} className="text-sm">{opt.label}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          </div>
          {isLoading && (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            </div>
          )}
        </section>
      </div>
    </AppLayout>
  );
};

export default Settings; 